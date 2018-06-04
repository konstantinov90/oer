<template>
  <div>
    <div style="display: flex; justify-content: space-around; padding: 6px;">
      <h3 style="width: 200px; display: flex; justify-items: center;">Тип сессии</h3>
      <div style="display: flex; justify-content: space-around; width: 250px;">
        <h3>Период</h3>
      </div>
      <div style="display: flex; justify-content: space-around; width: 50px;">
        <h3>Номер</h3>
      </div>
      <div style="display: flex; justify-content: space-around; width: 100px;">
        <h3>Статус</h3>
      </div>
    </div>
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
import { mapMutations, mapState } from 'vuex';
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
  mounted() {
    this.bid({ msg: null });
    this.allBids({ msg: null });
    this.sdd({ msg: null });
    this.allSdd({ msg: null });
  },
  methods: {
    ...mapMutations('common', ['bid', 'allBids', 'sdd', 'allSdd']),
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
