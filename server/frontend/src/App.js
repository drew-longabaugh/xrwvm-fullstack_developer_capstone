import LoginPanel from "./components/Login/Login"
import { Routes, Route } from "react-router-dom";

urlpatterns = [
    path('register/', TemplateView.as_view(template_name="index.html")),
]

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPanel />} />
    </Routes>
  );
}
export default App;
