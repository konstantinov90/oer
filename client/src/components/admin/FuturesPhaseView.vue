<template>
  <div>
    <button @click="makeRegistry">Выгрузить реестр МДП после сессии СДД</button>
    <button @click="uploadRegistry">Загрузить реестр МДП после биржевой сессии</button>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'FuturesPhaseView',
  computed: mapGetters('common', ['selectedSession']),
  methods: {
    makeRegistry() {
      this.$socket.sendObj({ type: 'futuresMakeRegistry', msg: this.selectedSession.sd_session_id });
    },
    uploadRegistry() {
      this.$socket.sendObj({ type: 'futuresUploadRegistry', msg: this.selectedSession._id });
    },
  },
};
</script>

<style>

</style>
