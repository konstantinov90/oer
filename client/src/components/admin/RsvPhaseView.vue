<template>
  <div>
    <button
      v-if="selectedSession.status === 'open'"
      @click="calculate">
      Провести расчет
    </button>
    <button
      v-if="selectedSession.status === 'closed'"
      @click="reopen">
      Переоткрыть сессию
    </button>
    <a
      href="#"
      @click="getFile">
      <img
        :src="xlsxImg"
        style="height: 32px;">
    </a>
    <bid-editor
      v-if="rioEntry && bid"
      :bid="bid"/>
  </div>
</template>

<script>
import axios from 'axios';
import { mapActions, mapGetters, mapState } from 'vuex';
import BidEditor from '../common/BidEditor.vue';
import xlsxImg from '../../../static/xlsx_96x3.png';

export default {
  name: 'RsvPhaseView',
  components: {
    BidEditor,
  },
  data() {
    return {
      xlsxImg,
    };
  },
  computed: {
    ...mapGetters('common', ['selectedSession']),
    ...mapState('common', ['bid', 'queringBid', 'rioEntry', 'spotResults']),
    filelink() {
      return `${IS_PROD ? __webpack_public_path__ : 'http://ats-konstantin1:8080/'}rest/bid_report/?session_id=${this.selectedSession._id}&username=admin`;
    },
  },
  created() {
    this.queryMgp();
  },
  methods: {
    ...mapActions('common', ['queryMgp']),
    calculate() {
      this.$socket.sendObj({ type: 'calculate', msg: this.selectedSession._id });
    },
    reopen() {
      this.$socket.sendObj({ type: 'reopen', msg: this.selectedSession._id });
    },
    getFile() {
      axios({
        url: this.filelink,
        method: 'GET',
        responseType: 'blob',
      }).then((response) => {
        const filename = response.headers['content-disposition'].split('=')[1].replace(/"/g, '');
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
      });
    },
  },
};
</script>

<style scoped>

</style>
