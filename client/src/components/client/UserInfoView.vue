<template>
  <div
    v-if="rioEntry"
    class="app__participant-info">
    <span>{{ rioEntry.name }}</span>
    <span>{{ username }}</span>
    <!-- <p class="app__participant-info__prop">Код участника:</p>
    <p class="app__participant-info__val"><code>{{ username }}</code></p>
    <p class="app__participant-info__prop">Страна:</p>
    <p class="app__participant-info__val"><code>{{ rioEntry.country_code }}</code></p>
    <p class="app__participant-info__prop">Наименование:</p>
    <p class="app__participant-info__val"><code>{{ rioEntry.name }}</code></p>
    <p class="app__participant-info__prop"/>
    <p class="app__participant-info__val"><code>{{ typeText }}</code></p> -->
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'UserInfoView',
  computed: {
    ...mapState('common', [
      'rioEntry',
      'username',
    ]),
    typeText() {
      return this.rioEntry.dir === 'buy' ? 'покупатель' : 'продавец';
    },
  },
};
</script>

<style>
  .app__participant-info {
    /* grid-area: info; */
    /* display: grid; */
    /* grid-template-columns: auto auto; */
    /* grid-auto-rows: 15px; */
    /* grid-gap: 8px; */
    /* align-items: center; */
    /* margin: 40px 0; */
    font-style: italic;
  }

  /* .app__participant-info__prop,
  .app__participant-info__val {
    margin: 0;
  }

  .app__participant-info__prop {
    justify-self: end;
  }

  .app__participant-info__val {
    justify-self: start;
  } */
</style>
