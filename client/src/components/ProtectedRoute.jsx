const ProtectedRoute = ({ children, isAuthenticated }) => {
  if (!isAuthenticated) {
    return <Login onLogin={() => {}} />;
  }
  return children;
};