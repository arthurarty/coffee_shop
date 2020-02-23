/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'arty-coffee-shop', // the auth0 domain prefix
    audience: 'coffee_shop', // the audience set for the auth0 app
    clientId: '5pbc86dIm37AzeDJdhZt8eruFohfGE6c', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
