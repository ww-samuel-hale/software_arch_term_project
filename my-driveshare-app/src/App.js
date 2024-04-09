import './App.css';
import { MyProvider } from './Context/Provider';
import NavBar from './Components/NavigationBar/NavBar';
import RoutePages from './Components/Routes/RoutePages';
import MessageDisplay from './Components/MessageDisplay/MessageDisplay'; // Update the path as needed
import { BrowserRouter } from 'react-router-dom';
import { useContext } from 'react';

function App() {
  return (
    <MyProvider>
      <BrowserRouter>
        <div className="App">
          <NavBar />
          <RoutePages />
        </div>
      </BrowserRouter>
    </MyProvider>
  );
}

export default App;
