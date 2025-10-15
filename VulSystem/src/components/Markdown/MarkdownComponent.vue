<template>
  <div class="markdown-content" :class="classname" v-html="parsedMarkdown"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, defineProps } from 'vue';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css'; // 可以根据喜好选择不同的代码高亮主题

// 定义 props
const props = defineProps<{
  markdown: string;
  classname?: string;
}>();

// 配置 marked 以使用 highlight.js 进行代码高亮
marked.use({
  renderer: {
    code(code: string, lang: string) {
      const language = hljs.getLanguage(lang || '') ? lang : 'plaintext';
      const highlighted = hljs.highlight(code, { language }).value;
      return `<pre><code class="hljs language-${language}">${highlighted}</code></pre>`;
    }
  }
});

// 计算属性，将 Markdown 转换为 HTML
const parsedMarkdown = computed(() => {
  return marked(props.markdown);
});

// 初始化代码高亮
onMounted(() => {
  const codeBlocks = document.querySelectorAll('pre code');
  codeBlocks.forEach((block) => {
    if (block instanceof HTMLElement) {
      hljs.highlightElement(block);
    }
  });
});
</script>

<style scoped>
/* 自定义 Markdown 样式 */
.markdown-content {
  font-family: Arial, sans-serif;
  line-height: 1.6;
}

.markdown-content h1 {
  font-size: 2em;
  margin-bottom: 0.5em;
}

.markdown-content h2 {
  font-size: 1.5em;
  margin-bottom: 0.5em;
}

.markdown-content p {
  margin-bottom: 1em;
}

.markdown-content pre {
  background-color: #f4f4f4;
  padding: 1em;
  border-radius: 4px;
  overflow-x: auto;
}

.markdown-content code {
  font-family: 'Courier New', Courier, monospace;
}
</style>
