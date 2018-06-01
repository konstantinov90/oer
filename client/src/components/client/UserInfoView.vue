<template>
  <div
    v-if="rioEntry"
    class="app__participant-info">
    <span
      :class="`sprite__flag_${flagClass}`"
      class="sprite sprite__flag"/>
    <span>{{ rioEntry.name }}</span>
    <span>{{ username }}</span>
    <span>{{ typeText }}</span>
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
import { mapGetters, mapState } from 'vuex';

export default {
  name: 'UserInfoView',
  computed: {
    ...mapGetters('common', ['username']),
    ...mapState('common', ['rioEntry']),
    typeText() {
      return this.rioEntry.dir === 'buy' ? 'потребитель' : 'поставщик';
    },
    flagClass() {
      switch (this.rioEntry.country_code) {
        case 'ARM':
          return 'armenia';
        case 'BLR':
          return 'belarus';
        case 'RUS':
          return 'russia';
        case 'KAZ':
          return 'kazakhstan';
        case 'KGZ':
          return 'kyrgyzstan';
        default:
          return null;
      }
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
    margin: 0 40px;
    display: flex;
    align-items: flex-end;
    flex-direction: column;
  }

  .app__participant-info * {
    margin: 2px 0;
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
