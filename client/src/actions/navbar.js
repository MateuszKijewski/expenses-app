import { CHANGE_ACTIVE_NAV } from './types';

export const setActiveNav = (link = '/') => dispatch => {
	dispatch({
		type: CHANGE_ACTIVE_NAV,
		payload: link
	});
};
