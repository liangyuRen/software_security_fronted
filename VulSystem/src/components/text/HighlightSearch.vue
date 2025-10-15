<!-- HighlightSearch.vue -->
<!--This is a reusable component that highlights the search query in the text.-->
<template>
  <span v-html="highlightedText"></span>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue';

const props = defineProps({
  text: {
    type: String,
    required: true
  },
  highlight: {
    type: String,
    required: true
  }
})

const highlightedText = computed(() => {
  if (!props.highlight) return props.text;

  // 将文本和高亮词转换为小写以忽略大小写
  const lowerText = props.text.toLowerCase();
  const lowerHighlight = props.highlight.toLowerCase();

  const isEqual = (charS: string, charT: string) => {
    if(charS === '(' && charT === '（') return true;
    if(charS === ')' && charT === '）') return true;
    return charS === charT;
  }

  // pre-build table
  const buildPartialMatchTable = (pattern: string) => {
    const table = new Array(pattern.length).fill(0);
    let prefixLength = 0;
    for (let i = 1; i < pattern.length; i++) {
      while (prefixLength > 0 && !isEqual(pattern[i], pattern[prefixLength])) {
        prefixLength = table[prefixLength - 1];
      }
      if (isEqual(pattern[i], pattern[prefixLength])) {
        prefixLength++;
      }
      table[i] = prefixLength;
    }
    return table;
  };

  // KMP search
  const kmpSearch = (text: string, pattern: string) => {
    const table = buildPartialMatchTable(pattern);
    const matches = [];
    let j = 0;
    for (let i = 0; i < text.length; i++) {
      while (j > 0 && !isEqual(text[i], pattern[j])) {
        j = table[j - 1];
      }
      if (isEqual(text[i], pattern[j])) {
        j++;
      }
      if (j === pattern.length) {
        matches.push(i - pattern.length + 1);
        j = table[j - 1];
      }
    }
    return matches;
  };

  const matches = kmpSearch(lowerText, lowerHighlight);
  if (matches.length === 0) return props.text;
  let result = '';
  let lastIndex = 0;
  for (const matchIndex of matches) {
    result += props.text.slice(lastIndex, matchIndex);
    result += `<span class="highlight bounce-animation">${props.text.slice(matchIndex, matchIndex + props.highlight.length)}</span>`;
    lastIndex = matchIndex + props.highlight.length;
  }
  result += props.text.slice(lastIndex);

  return result;
});


watch(() => props.highlight, () => {
  // remove and add class to trigger animation
  const elements = document.getElementsByClassName('highlight');
  Array.from(elements).forEach(element => {
    if (element instanceof HTMLElement) {
      element.classList.remove('bounce-animation');
      // trigger reflow
      void element.offsetWidth;
      element.classList.add('bounce-animation');
    }
  });
})
</script>

<style scoped>
@keyframes bounce {
  0% {
    transform: translateY(-1px);
  }
  10%, 30% {
    transform: translateY(-4px);
  }
  100% {
    transform: translateY(0);
  }
}

:deep(.highlight) {
  background-color: rgba(255, 245, 102, 0.7);
  padding: 0 2px;
  margin: 0 1px;
  border-radius: 4px;
  display: inline-block;
}

:deep(.bounce-animation) {
  animation: bounce 0.4s ease;
}
</style>
