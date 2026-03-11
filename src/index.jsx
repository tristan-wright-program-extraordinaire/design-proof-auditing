
import ReactDOM from 'react-dom'

import Application from './components/Application'

import './index.sass'


const App = function () {
  return (
    <Application />
  )
}

const view = App('pywebview')

const element = document.getElementById('app')
ReactDOM.render(view, element)

export default App