<template>
  <div
    :class="indicatorClass"
    class="server-state-indicator"
  >
    <p class="server-state-indicator__label">
      {{ `Server ${serverState ? 'online' : 'offline'}` }}
    </p>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'ServerStateIndicator',
  computed: {
    indicatorClass() {
      return {
        'server-state-indicator__server-active': this.serverState,
        'server-state-indicator__server-unavailible': !this.serverState,
      };
    },
    ...mapState('common', {
      serverState: ({ socket }) => socket.isConnected,
    }),
  },
};
</script>

<style lang="stylus">
.server-state-indicator
  text-align center
  width 60px
  height 60px
  border-radius 60px
  display grid
  grid-template-areas 'a'
  align-content center
  justify-content center
  z-index 1000
  opacity 0.8

  &__server-active
    background radial-gradient(green, yellowgreen)

  &__server-unavailible
    background radial-gradient(red, yellowgreen)

.server-state-indicator__label
  grid-area a
  font-size 0.8em
  color #eaeaea

</style>
