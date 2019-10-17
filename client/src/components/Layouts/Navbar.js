import React from 'react';
import styled from 'styled-components';
import { primaryColor, secondColor } from '../../utility/colors';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { setActiveNav } from '../../actions/navbar';
// ** STYLING

const NavbarWrapper = styled.div`
	display: flex;
	flex-direction: column;
	flex: 0 0 6rem;
	position: -webkit-sticky;
	position: sticky;
	top: 0;
	height: 100vh;
	font-size: 20px;
	background: ${props => (props.primary ? primaryColor : 'white')};
	color: #fff;
`;
const IconWrapper = styled.div`padding-top: 50%;`;
const IconButton = styled(Link)`
	box-sizing: border-box;
	border-right: 4px solid ${props => (props.active ? secondColor : 'rgba(0,0,0,0)')};
	margin: 40px 0;
	height: 34px;
	flex-shrink: 0;
	width: 100%;
	font-size: inherit;
	font-weight: inherit;
	background: none;

	color: inherit;
	display: flex;
	justify-content: center;
	align-items: center;
	cursor: pointer;
	&:hover {
		border-right: 4px solid ${secondColor};
	}

	:first-child {
		margin: 0;
	}
	//
`;
//***

const Navbar = ({ setActiveNav, activeLink }) => {
	console.log(typeof activeLink);
	const links = [ 'dashboard', 'bill', 'cash', 'login', 'register'];
	const iconLink = links.map(link => (
		<IconButton onClick={() => setActiveNav(link)} to={`/${link}`} alt={link} active={link === activeLink}>
			{' '}
			<img src={require(`../../assets/${link}.svg`)} alt={link} />{' '}
		</IconButton>
	));
	return (
		<NavbarWrapper primary>
			<IconWrapper>{iconLink}</IconWrapper>
		</NavbarWrapper>
	);
};

Navbar.propTypes = {
	setActiveNav: PropTypes.func.isRequired,
	activeLink: PropTypes.string.isRequired
};
const mapStateToProps = state => ({
	activeLink: state.navbarReducer.activeLink
});

export default connect(mapStateToProps, { setActiveNav })(Navbar);
