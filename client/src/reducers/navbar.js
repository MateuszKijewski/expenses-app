import { CHANGE_ACTIVE_NAV } from '../actions/types';

const initialStore = {
	activeLink: 'bill'
};

export default function(state = initialStore, action) {
	const { type, payload } = action;

	switch (type) {
		case CHANGE_ACTIVE_NAV:
			return { ...state, activeLink: payload };
			break;

		default:
			return state;
			break;
	}
}
