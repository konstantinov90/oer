<template>
  <app-layout class="admin">
    <h1>Администрирование</h1>
    <date-view
      v-if="selectedSession"
      :dates="[selectedSession.startDate, selectedSession.finishDate]"/>
    <div class="admin__wrapper">
      <div class="admin__content">
        <router-view/>
      </div>
      <div class="admin__info">
        <user-list-view />
      </div>
    </div>
  </app-layout>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import AppLayout from '../common/AppLayout.vue';
import PhaseSelector from './PhaseSelector.vue';
import DateView from '../common/DateView.vue';
import PhaseView from '../common/PhaseView.vue';
import UserListView from './UserListView.vue';

import StartPhaseView from './StartPhaseView.vue';
import AcceptingBidsPhaseView from './AcceptingBidsPhaseView.vue';
import SddPhaseView from './SddPhaseView.vue';

export default {
  name: 'Admin',
  components: {
    AppLayout,
    DateView,
    PhaseSelector,
    PhaseView,
    UserListView,
    StartPhaseView,
    SddPhaseView,
    AcceptingBidsPhaseView,
  },
  computed: {
    ...mapState('common', ['adminSession', 'phase', 'selectedSession']),
    ...mapGetters('common', ['selectedSession']),
  },
  created() {
    if (!this.adminSession) {
      this.$router.push({ name: 'app' });
    }
  },
};
</script>

<style>
.admin__wrapper {
  display: grid;
  grid-template-areas: "content info";
  grid-template-columns: 4fr 1fr;
}

.admin__content {
  grid-area: content;
}

.admin__info {
  grid-area: info;
}

</style>
