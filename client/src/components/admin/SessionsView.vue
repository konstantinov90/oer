<template>
  <div>
    <start-phase-view/>
    <router-link
      v-for="(session, idx) in sessions"
      :key="idx"
      :to="getLink(session)">
      <session-item :session="session"/>
    </router-link>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import StartPhaseView from './StartPhaseView.vue';
import SessionItem from '../common/SessionItem.vue';

const links = {
  free: 'sddAdmin',
  futures: 'futuresAdmin',
  spot: 'rsvAdmin',
};

export default {
  name: 'SessionsView',
  components: {
    SessionItem,
    StartPhaseView,
  },
  computed: {
    ...mapState('common', ['sessions']),
  },
  methods: {
    getLink(session) {
      const name = links[session.type];
      return { name, params: { id: session._id } };
    },
  },
};
</script>

<style>

</style>