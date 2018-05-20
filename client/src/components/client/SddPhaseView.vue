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
    <div v-if="editorVisible">
      <div
        :style="`height: ${backgroundHeight}`"
        class="modal-background"/>
      <div class="modal-foreground">
        <sdd-editor
          :close-fn="toggleEditorVisible"/>
      </div>
    </div>
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
      backgroundHeight: '100%',
    };
  },
  computed: {
    ...mapGetters('common', ['selectedSession']),
  },
  created() {
    window.addEventListener('scroll', this.updateBackgroundHeight);
  },
  destroyed() {
    window.removeEventListener('scroll', this.updateBackgroundHeight);
  },
  methods: {
    updateBackgroundHeight() {
      this.backgroundHeight = `${window.innerHeight + window.pageYOffset}px`;
    },
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
  margin: 0 48%;
}

.modal-background {
  position: absolute;
  top: 0;
  /* bottom: 0; */
  left: 0;
  right: 0;
  background: black;
  opacity: 0.4;
}

.modal-foreground {
  position: absolute;
  top: 0;
  /* bottom: 0; */
  left: 0;
  right: 0;
  background: white;
  margin: 40px;
  padding: 20px;
}
</style>
