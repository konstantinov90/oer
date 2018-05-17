<template>
  <div>
    <h2>Свободные договоры (СД)</h2>
    <date-view
      v-if="selectedSession"
      :dates="[selectedSession.startDate, selectedSession.finishDate]"/>
    <button
      v-if="!editorVisible"
      class="new-sdd-btn"
      @click="toggleEditorVisible">
      +
    </button>
    <sdd-list-view />
    <sdd-editor
      v-if="editorVisible"
      :close-fn="toggleEditorVisible"/>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import SddListView from '../common/SddListView.vue';
import SddEditor from '../common/SddEditor.vue';
import DateView from '../common/DateView.vue';

export default {
  name: 'SddPhaseView',
  components: {
    SddListView,
    SddEditor,
    DateView,
  },
  data() {
    return {
      editorVisible: false,
    };
  },
  computed: {
    ...mapGetters('common', ['selectedSession']),
  },
  methods: {
    toggleEditorVisible() {
      this.editorVisible = !this.editorVisible;
    },
  },
};
</script>

<style>
.new-sdd-btn {
  height: 48px;
  width: 48px;
  border-radius: 24px;
  font-size: 40px;
  background: coral;
  color: white;
  box-shadow: 3px 3px gray;
  margin: 0 50%;
}
</style>
