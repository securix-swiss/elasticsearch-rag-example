import { useEffect, useState } from 'react'
import { Sources } from './sources'
import { ChatMessageType } from '../../types'
import { marked, Renderer } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

interface AnswerMessageProps {
  text: ChatMessageType['content']
  sources: ChatMessageType['sources']
  onSourceClick: (source: string) => void
}

export const AnswerMessage: React.FC<AnswerMessageProps> = ({
  text,
  sources,
  onSourceClick,
}) => {
  const [parsedText, setParsedText] = useState<string>('')

  useEffect(() => {
    const parseMarkdown = async () => {
      if (text) {
        const breakText = text.replace(/CMD__NEWLINE__CHAT/g, '\n')

        // Create a custom renderer for marked
        const renderer = new Renderer()

        // Customize how code blocks are handled
        renderer.code = ({ text = '', lang = '' }) => {
          const validLang = hljs.getLanguage(lang) ? lang : 'plaintext'
          const highlighted = hljs.highlight(text, { language: validLang }).value
          return `<pre><code class="hljs ${validLang}">${highlighted}</code></pre>`
        }

        marked.setOptions({
          gfm: true,
          breaks: true,
          renderer, // Use the custom renderer
        })

        const result = await marked(breakText)
        setParsedText(result)
      }
    }
    parseMarkdown()
  }, [text])

  return (
    <div className="mb-4">
      <header className="flex flex-row justify-between mb-8">
        <div className="flex flex-row justify-center align-middle items-center">
          <div className="flex flex-col justify-start">
            <h2 className="text-zinc-700 text-2xl font-bold leading-9">
              Answer
            </h2>
            <p className="text-zinc-400 text-sm font-medium">
              Powered by <b>Elasticsearch</b>
            </p>
          </div>
        </div>
      </header>

      {parsedText && (
        <div
          className="leading-tight text-gray-800 mb-8"
          dangerouslySetInnerHTML={{ __html: parsedText }}
        ></div>
      )}
      {sources && (
        <Sources
          showDisclaimer
          sources={sources}
          onSourceClick={onSourceClick}
        />
      )}
    </div>
  )
}
