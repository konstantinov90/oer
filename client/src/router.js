import VueRouter from 'vue-router';

import AppRoot from './components/AppRoot.vue';
import App from './components/client/App.vue';
import SddPhaseView from './components/client/SddPhaseView.vue';
import RsvPhaseView from './components/client/RsvPhaseView.vue';
import FuturesPhaseView from './components/client/FuturesPhaseView.vue';
import SessionsView from './components/client/SessionsView.vue';
import SddAdminView from './components/admin/SddPhaseView.vue';
import RsvAdminView from './components/admin/RsvPhaseView.vue';
import FuturesAdminView from './components/admin/FuturesPhaseView.vue';
import SessionsAdminView from './components/admin/SessionsView.vue';
import Admin from './components/admin/Admin.vue';
import Login from './components/Login.vue';
import Placeholder from './components/Placeholder.vue';

function modPath(path) {
  return `${__webpack_public_path__}${path}`;
}

const routes = [
  {
    path: modPath('/'),
    name: 'root',
    component: AppRoot,
    children: [
      { path: 'login', name: 'login', component: Login },
      {
        path: 'admin',
        name: 'admin',
        component: Admin,
        children: [
          { path: '/', name: 'sessionsAdmin', component: SessionsAdminView },
          { path: 'sdd/:id', name: 'sddAdmin', component: SddAdminView },
          { path: 'rsv/:id', name: 'rsvAdmin', component: RsvAdminView },
          { path: 'futures/:id', name: 'futuresAdmin', component: FuturesAdminView },
        ],
      },
      {
        path: 'app',
        name: 'app',
        component: App,
        children: [
          { path: '/', name: 'sessions', component: SessionsView },
          { path: 'sdd/:id', name: 'sdd', component: SddPhaseView },
          { path: 'rsv/:id', name: 'rsv', component: RsvPhaseView },
          { path: 'futures/:id', name: 'futures', component: FuturesPhaseView },
        ],
      },
      { path: '*', name: 'placeholder', component: Placeholder },
    ],
  },
];

export default new VueRouter({
  mode: 'history',
  routes,
});
