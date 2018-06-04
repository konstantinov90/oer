<template>
  <div
    class="sdd-list">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <multiselect
        v-model="value"
        :multiple="true"
        :close-on-select="false"
        :clear-on-select="false"
        :hide-selected="true"
        :options="options"
        :preserve-search="true"
        class="sdd_list__multiselect-wrapper"
        placeholder="фильтр"
        label="description"
        select-label=""
        selected-label=""
        deselect-label=""
        track-by="description">
        <template
          slot="tag"
          slot-scope="props">
          <span class="custom__tag">
            <span>{{ props.option.description }}</span>
            <span
              class="custom__remove"
              @click="props.remove(props.option)">
              <b>&times;</b>
            </span>
          </span>
        </template>
      </multiselect>
      <a
        v-if="selectedSession.status === 'closed'"
        href="#"
        @click="getFile">
        <img
          :src="xlsxImg"
          style="height: 32px;">
      </a>
    </div>
    <sdd-view
      v-for="sd in sddFiltered"
      :key="sd._id"
      :collapsed="isCollapsed(sd._id)"
      :on-click="() => toggleCollapse(sd._id)"
      :sdd="sd"/>
  </div>
</template>

<script>
import axios from 'axios';
import { mapGetters, mapActions, mapState } from 'vuex';
import Multiselect from 'vue-multiselect';
import SddView from './SddView.vue';
import xlsxImg from '../../../static/xlsx_96x3.png';

export default {
  name: 'SddListView',
  components: {
    Multiselect,
    SddView,
  },
  data() {
    const options = [
      { status: 'created', description: 'проекты' },
      { status: 'negotiation', description: 'согласования' },
      { status: 'registered', description: 'зарегистрированные' },
      { status: 'rejected', description: 'отклоненные' },
    ];
    return {
      xlsxImg,
      collapsed: [],
      options,
      value: [...options],
    };
  },
  computed: {
    ...mapState('common', ['sdd', 'queringSdd']),
    ...mapGetters('common', ['selectedSession', 'username']),
    sddFiltered() {
      const values = this.value.map(({ status }) => status);
      return this.sdd ? this.sdd.filter(sd => values.includes(sd.status)) : [];
    },
    filelink() {
      return `${IS_PROD ? __webpack_public_path__ : 'http://ats-konstantin1:8080/'}rest/sdd_report/?session_id=${this.selectedSession._id}&username=${this.username || 'admin'}`;
    },
  },
  created() {
    this.querySdd();
  },
  methods: {
    ...mapActions('common', ['querySdd']),
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
    isCollapsed(id) {
      return !this.collapsed.includes(id);
    },
    toggleCollapse(id) {
      const idx = this.collapsed.indexOf(id);
      if (idx === -1) {
        this.collapsed = [...this.collapsed, id];
      } else {
        this.collapsed = [...this.collapsed.slice(0, idx), ...this.collapsed.slice(idx + 1)];
      }
    },
  },
};
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style>
.sdd-list {
  margin-top: 10px;
  min-height: 300px;
}

.custom__tag {
  border: 1px solid black;
  border-radius: 16px;
  padding: 3px 8px;
  background: #eff;
  margin: 0 5px;
}

.custom__remove:hover {
  cursor: pointer;
}

.sdd_list__multiselect-wrapper {
  width: 70%;
}
</style>
