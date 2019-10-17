import { createStore, applyMiddleware, compose } from 'redux';
import { composeWithDevTools } from 'redux-devtools-extension';
import thunk from 'redux-thunk';
import rootReducer from './reducers/index';
import navbarReducer from './reducers/navbar';

let composeEnhancers = compose;


const store = createStore(rootReducer, composeWithDevTools(applyMiddleware(thunk)));

export default store;
//
