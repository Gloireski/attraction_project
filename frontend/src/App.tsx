// ...
import Home from "./routes/home";
import { Route, Routes } from "react-router";

export default function App() {
  return (
    <Routes>
      {/* <Route path="/about" element={<About />} /> */}
      <Route path="/" element={<Home />} />
    </Routes>
  );
}
