<template>
  <div class="user-list">
    <template
      v-for="(isOnline, client, idx) in clients"
      v-if="client !== 'admin'">
      <div
        :class="getClass(client)"
        :key="client"
        class="user-list__item">
        <a
          href="#"
          @click="queryUserBid(client)">
          {{ client }}
        </a>
      </div>
      <p
        :key="idx"
        class="user-list__status">
        {{ isOnline ? '🌍' : '❓' }}
      </p>
    </template>
  </div>
</template>

<script>
import { mapActions, mapMutations, mapState } from 'vuex';

export default {
  name: 'UserListView',
  computed: mapState('admin', [
    'clients',
    'selectedUser',
  ]),
  methods: {
    ...mapMutations('admin', ['selectUser']),
    ...mapActions('common', ['queryBid']),
    getClass(user) {
      return {
        'user-list__item_selected': user === this.selectedUser,
      };
    },
    queryUserBid(username) {
      this.selectUser(username);
      this.queryBid(username);
    },
  },
};
</script>

<style scoped>
.user-list {
  display: grid;
  grid-template-columns: auto auto;
  grid-auto-rows: 20px;
  grid-gap: 8px;
  overflow: hidden;
}

.user-list__item,
.user-list__status {
  margin: 0;
}

.user-list__item {
  justify-self: end;
}

.user-list__status {
  justify-self: start;
}

.user-list__item_selected {
  position: relative;
}

.user-list__item_selected:after {
  content: '';
  height: 100%;
  width: 300%;
  overflow: hidden;
  background: linear-gradient(to left, white, gray, black, gray, white);
  display: block;
  bottom: 0;
  left: -70%;
  position: absolute;
  opacity: 0.3;
  border-radius: 4px;
  z-index: 1;
}
</style>
