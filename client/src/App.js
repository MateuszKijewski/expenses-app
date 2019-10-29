import React from 'react';
import { Provider } from 'react-redux';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';

import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { bgColor } from './utility/colors';
import { gridWithNavbar, gridWithOutNavbar } from './utility/settings';
import './App.css';
// ** COMPONENTS
import Dashboard from './components/Dashboard';
import Bill from './components/Bill';
import Login from './components/Login';

//* LAYOUTS
import Navbar from './components/Layouts/Navbar';

const ProviderWrapper = styled.div`
	display: grid;
	grid-template-columns: ${props => (props.isRootPath ? `1fr` : `100px 1fr`)};
`;

const ContentWrapper = styled.div`
	display: flex;
	height: 100vh;
	width: 100%;
	background: ${bgColor};
	box-sizing: border-box;
`;

const App = ({ activeLink }) => {
	console.log(activeLink);
	const isRootPath = [ 'login', 'register' ].indexOf(activeLink) != -1 ? true : false;
	console.log(isRootPath);
	return (
		<Router>
			<ProviderWrapper isRootPath={isRootPath}>
				{isRootPath ? null : <Navbar />}
				<ContentWrapper>
					<Switch>
						{/* <Route exact path="/" component={props => <Login {...props} />} /> */}
						<Route exact path="/login" component={props => <Login {...props} />} />
						<Route exact path="/register" component={props => <Login {...props} />} />
						<Route exact path="/dashboard" component={props => <Dashboard {...props} />} />
						<Route exact path="/bill" component={props => <Bill {...props} />} />
					</Switch>
				</ContentWrapper>
			</ProviderWrapper>
		</Router>
	);
};

App.propTypes = {
	activeLink: PropTypes.string.isRequired
};
const mapStateToProps = state => ({
	activeLink: state.navbarReducer.activeLink
});

export default connect(mapStateToProps)(App);
