import logo from './logo.svg';
import './App.css';
import { MyProvider } from './Context/Provider';

function App() {
  return (
    <MyProvider>
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
        </header>
      </div>
    </MyProvider>
  );
}

export default App;
