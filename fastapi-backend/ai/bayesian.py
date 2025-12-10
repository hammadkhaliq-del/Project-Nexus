"""
Bayesian Network Engine - Probabilistic Reasoning for Event Prediction
Predicts accidents and emergencies using conditional probabilities
"""
from typing import Dict, Tuple, List
from dataclasses import dataclass
import random

from core.city import City, Weather
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class BayesianEvent:
    """Predicted event with probability"""
    event_type: str
    probability: float
    position: Tuple[int, int]
    tick: int
    factors: Dict[str, any]


class BayesianNetwork:
    """
    AI Engine #5: Bayesian Network for Event Prediction
    
    Network Structure:
    
    Weather → Accident
    Rush Hour → Accident  
    Traffic Density → Accident
    
    Example:
    P(Accident | Rain, Rush Hour, High Traffic) = 0.66
    
    The network uses conditional probability tables (CPTs) to model
    how different factors influence accident likelihood
    """
    
    def __init__(self, city: City):
        self.city = city
        self.base_accident_rate = settings.ACCIDENT_BASE_RATE
        self.base_fire_rate = settings.EMERGENCY_SPAWN_RATE
        
        # Conditional Probability Tables
        self.cpts = self._initialize_cpts()
        
        # Prediction history
        self.predictions: List[BayesianEvent] = []
        self.prediction_accuracy: Dict[str, float] = {
            "accident": 0.0,
            "fire": 0.0
        }
        
        logger.info("Bayesian Network initialized")
    
    def _initialize_cpts(self) -> Dict[str, Dict]:
        """Initialize Conditional Probability Tables"""
        return {
            # P(Accident | Weather)
            "accident_weather": {
                Weather.CLEAR: 1.0,
                Weather.RAIN: 2.5,
                Weather.SNOW: 3.0
            },
            
            # P(Accident | Rush Hour)
            "accident_rush_hour": {
                True: 2.0,   # During rush hour
                False: 1.0   # Normal time
            },
            
            # P(Accident | Traffic Density)
            "accident_traffic": {
                "low": 0.5,      # < 3 vehicles nearby
                "medium": 1.0,   # 3-5 vehicles
                "high": 1.8      # > 5 vehicles
            },
            
            # P(Fire | Weather) - dry weather increases fire risk
            "fire_weather": {
                Weather.CLEAR: 1.2,
                Weather.RAIN: 0.3,   # Rain reduces fire risk
                Weather.SNOW: 0.5
            },
            
            # P(Fire | Building Density)
            "fire_density": {
                "low": 0.8,
                "medium": 1.0,
                "high": 1.5   # More buildings = higher risk
            }
        }
    
    def predict_accident(self, tick: int, num_vehicles: int) -> Tuple[bool, float, Dict]:
        """
        Predict if accident will occur using Bayesian inference
        
        Returns:
            (should_spawn, probability, factors)
        """
        # Identify factors
        weather = self.city.weather
        is_rush_hour = self._is_rush_hour(tick)
        traffic_density = self._classify_traffic_density(num_vehicles)
        
        # Calculate conditional probabilities
        p_weather = self.cpts["accident_weather"][weather]
        p_rush_hour = self.cpts["accident_rush_hour"][is_rush_hour]
        p_traffic = self.cpts["accident_traffic"][traffic_density]
        
        # Combined probability using Bayes' rule (simplified)
        # P(Accident | Evidence) ∝ P(Evidence | Accident) * P(Accident)
        combined_multiplier = p_weather * p_rush_hour * p_traffic
        final_probability = self.base_accident_rate * combined_multiplier
        
        # Cap at reasonable maximum
        final_probability = min(final_probability, 0.75)
        
        # Stochastic decision
        should_spawn = random.random() < final_probability
        
        factors = {
            "weather": weather.value,
            "is_rush_hour": is_rush_hour,
            "traffic_density": traffic_density,
            "p_weather": p_weather,
            "p_rush_hour": p_rush_hour,
            "p_traffic": p_traffic,
            "final_probability": final_probability
        }
        
        if should_spawn:
            logger.info(
                f"Bayesian: Accident predicted (P={final_probability:.3f}). "
                f"Factors: Weather={weather.value}, RushHour={is_rush_hour}, "
                f"Traffic={traffic_density}"
            )
        
        return should_spawn, final_probability, factors
    
    def predict_fire(self, tick: int) -> Tuple[bool, float, Dict]:
        """
        Predict if fire will occur using Bayesian inference
        
        Returns:
            (should_spawn, probability, factors)
        """
        # Identify factors
        weather = self.city.weather
        building_density = self._classify_building_density()
        
        # Calculate conditional probabilities
        p_weather = self.cpts["fire_weather"][weather]
        p_density = self.cpts["fire_density"][building_density]
        
        # Combined probability
        combined_multiplier = p_weather * p_density
        final_probability = self.base_fire_rate * combined_multiplier
        
        # Cap at reasonable maximum
        final_probability = min(final_probability, 0.50)
        
        # Stochastic decision
        should_spawn = random.random() < final_probability
        
        factors = {
            "weather": weather.value,
            "building_density": building_density,
            "p_weather": p_weather,
            "p_density": p_density,
            "final_probability": final_probability
        }
        
        if should_spawn:
            logger.info(
                f"Bayesian: Fire predicted (P={final_probability:.3f}). "
                f"Factors: Weather={weather.value}, Density={building_density}"
            )
        
        return should_spawn, final_probability, factors
    
    def _is_rush_hour(self, tick: int) -> bool:
        """
        Determine if current time is rush hour
        Simulate morning (ticks 200-300) and evening (ticks 600-700) rush hours
        """
        tick_mod = tick % 1000  # Daily cycle
        return (200 <= tick_mod <= 300) or (600 <= tick_mod <= 700)
    
    def _classify_traffic_density(self, num_vehicles: int) -> str:
        """Classify traffic density based on active vehicles"""
        if num_vehicles < 3:
            return "low"
        elif num_vehicles <= 5:
            return "medium"
        else:
            return "high"
    
    def _classify_building_density(self) -> str:
        """Classify building density in city"""
        num_buildings = len(self.city.buildings)
        
        if num_buildings < 10:
            return "low"
        elif num_buildings <= 20:
            return "medium"
        else:
            return "high"
    
    def record_prediction(self, event: BayesianEvent):
        """Record a prediction for accuracy tracking"""
        self.predictions.append(event)
        
        # Limit history
        if len(self.predictions) > 100:
            self.predictions = self.predictions[-100:]
    
    def get_network_state(self) -> dict:
        """Get current Bayesian network state"""
        return {
            "base_accident_rate": self.base_accident_rate,
            "base_fire_rate": self.base_fire_rate,
            "weather": self.city.weather.value,
            "weather_accident_multiplier": self.cpts["accident_weather"][self.city.weather],
            "weather_fire_multiplier": self.cpts["fire_weather"][self.city.weather],
            "total_predictions": len(self.predictions)
        }
    
    def generate_explanation(
        self,
        event_type: str,
        probability: float,
        factors: Dict
    ) -> str:
        """Generate natural language explanation of prediction"""
        if event_type == "accident":
            explanation = (
                f"Bayesian Network predicted accident with P={probability:.3f}. "
                f"Inference based on: Weather={factors['weather']} "
                f"(multiplier: {factors['p_weather']:.2f}), "
                f"Rush Hour={factors['is_rush_hour']} "
                f"(multiplier: {factors['p_rush_hour']:.2f}), "
                f"Traffic Density={factors['traffic_density']} "
                f"(multiplier: {factors['p_traffic']:.2f}). "
                f"Using Bayes' rule: P(Accident|Evidence) ∝ P(Evidence|Accident) × P(Accident). "
                f"Base rate: {self.base_accident_rate:.3f}, "
                f"Combined multiplier: {factors['p_weather'] * factors['p_rush_hour'] * factors['p_traffic']:.2f}"
            )
        else:  # fire
            explanation = (
                f"Bayesian Network predicted fire with P={probability:.3f}. "
                f"Inference based on: Weather={factors['weather']} "
                f"(multiplier: {factors['p_weather']:.2f}), "
                f"Building Density={factors['building_density']} "
                f"(multiplier: {factors['p_density']:.2f}). "
                f"Base rate: {self.base_fire_rate:.3f}, "
                f"Combined multiplier: {factors['p_weather'] * factors['p_density']:.2f}"
            )
        
        return explanation
    
    def update_cpt(self, table_name: str, key: any, value: float):
        """Update a conditional probability table entry (for learning)"""
        if table_name in self.cpts and key in self.cpts[table_name]:
            self.cpts[table_name][key] = value
            logger.info(f"CPT updated: {table_name}[{key}] = {value}")