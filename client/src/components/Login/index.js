import React from 'react';
import styled from 'styled-components';

import Logo from '../../assets/modern.svg';

const FlexWrapper = styled.div`
	display: flex;
	padding: 50px;
	justify-content: center;
	align-items: center;
	width: 80%;
	margin: 0 auto;
`;

const InputText = styled.input`
	border: none;
	font-size: 16px;
	color: #333;
	line-height: 1.2;
	display: block;
	width: 100%;
	height: 55px;
	background: 0 0;
	padding: 0 7px 0 43px;
`;
const InputWrap = styled.div`
	width: 100%;
	position: relative;
	border-bottom: 2px solid #d9d9d9;
`;
const LoginWrapper = styled.div`flex-basis: 50%;`;
const ImgLogo = styled.div`flex-basis: 50%;`;
const Login = props => {
	console.log(props);
	return (
		<FlexWrapper>
			<LoginWrapper>
				<div className="container">
					<InputWrap>
						<label for="uname">
							<b>Username</b>
						</label>
						<InputText type="text" placeholder="Enter Username" name="uname" required />
					</InputWrap>

					<label for="psw">
						<b>Password</b>
					</label>
					<InputText type="password" placeholder="Enter Password" name="psw" required />

					<button type="submit">Login</button>
					<label>
						<InputText type="checkbox" checked="checked" name="remember" /> Remember me
					</label>
				</div>
				{/* 
  <div className="container" style="background-color:#f1f1f1">
    <button type="button" className="cancelbtn">Cancel</button>
    <span className="psw">Forgot <a href="#">password?</a></span>
  </div> */}
			</LoginWrapper>

			<ImgLogo>
				<img src={Logo} alt="logo" />
			</ImgLogo>
		</FlexWrapper>
	);
};

export default Login;
