<template>
  <div>
    <h2>Сессии</h2>
    <router-link
      v-for="(session, idx) in sessions"
      :key="idx"
      :to="getLink(session)"
      class="session-link">
      <session-item :session="session"/>
    </router-link>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import SessionItem from '../common/SessionItem.vue';

const links = {
  free: 'sdd',
  futures: 'futures',
  spot: 'rsv',
};

export default {
  name: 'SessionsView',
  components: {
    SessionItem,
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
.session-link {
  text-decoration: none;
}
</style>
