import { createI18n } from 'vue-i18n'
import zh from './zh'
import en from './en'

// 从localStorage获取保存的语言设置，如果没有则使用浏览器语言
const getDefaultLocale = (): string => {
  const savedLanguage = localStorage.getItem('language')
  if (savedLanguage) {
    return savedLanguage
  }

  // 根据浏览器语言设置默认语言
  const browserLanguage = navigator.language || (navigator as any).userLanguage
  if (browserLanguage.startsWith('en')) {
    return 'en'
  }

  return 'zh' // 默认中文
}

const i18n = createI18n({
  legacy: false,
  locale: getDefaultLocale(),
  fallbackLocale: 'zh',
  messages: {
    zh,
    en
  }
})

export default i18n