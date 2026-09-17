/**
 * AuthClient — Client-side JWT, localStorage, sessionStorage, and cookie state manager.
 */
const AuthClient = {
    STORAGE_KEY_TOKEN: 'auth_token',
    STORAGE_KEY_USER: 'user_info',
    COOKIE_NAME: 'jwt_token',

    /**
     * Sets session data across localStorage, sessionStorage, and HTTP cookie.
     */
    setSession(token, user) {
        if (token) {
            localStorage.setItem(this.STORAGE_KEY_TOKEN, token);
            sessionStorage.setItem(this.STORAGE_KEY_TOKEN, token);
            this.setCookie(this.COOKIE_NAME, token, 7);
        }
        if (user) {
            const userStr = typeof user === 'string' ? user : JSON.stringify(user);
            localStorage.setItem(this.STORAGE_KEY_USER, userStr);
            sessionStorage.setItem(this.STORAGE_KEY_USER, userStr);
        }
    },

    /**
     * Clears session state from localStorage, sessionStorage, and cookies.
     */
    clearSession() {
        localStorage.removeItem(this.STORAGE_KEY_TOKEN);
        localStorage.removeItem(this.STORAGE_KEY_USER);
        sessionStorage.removeItem(this.STORAGE_KEY_TOKEN);
        sessionStorage.removeItem(this.STORAGE_KEY_USER);
        this.deleteCookie(this.COOKIE_NAME);
    },

    /**
     * Retrieves token from localStorage, sessionStorage, or document cookie.
     */
    getToken() {
        return localStorage.getItem(this.STORAGE_KEY_TOKEN) ||
               sessionStorage.getItem(this.STORAGE_KEY_TOKEN) ||
               this.getCookie(this.COOKIE_NAME);
    },

    /**
     * Retrieves user object from localStorage or sessionStorage.
     */
    getUser() {
        const raw = localStorage.getItem(this.STORAGE_KEY_USER) || sessionStorage.getItem(this.STORAGE_KEY_USER);
        if (!raw) return null;
        try {
            return JSON.parse(raw);
        } catch (e) {
            return null;
        }
    },

    /**
     * Helper for setting cookies.
     */
    setCookie(name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Lax";
    },

    /**
     * Helper for getting cookie.
     */
    getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    },

    /**
     * Helper for deleting cookie.
     */
    deleteCookie(name) {
        document.cookie = name + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT; SameSite=Lax';
    },

    /**
     * Intercepts fetch requests to automatically append Authorization header if token exists.
     */
    initFetchInterceptor() {
        const originalFetch = window.fetch;
        const self = this;
        window.fetch = function(resource, config = {}) {
            const token = self.getToken();
            if (token) {
                config.headers = config.headers || {};
                if (!config.headers['Authorization']) {
                    config.headers['Authorization'] = 'Bearer ' + token;
                }
            }
            return originalFetch(resource, config);
        };
    }
};

// Initialize client-side auth synchronization
document.addEventListener('DOMContentLoaded', () => {
    AuthClient.initFetchInterceptor();
});
