'use client';

type MarkdownViewerProps = {
  content: string;
  title?: string;
};

export function MarkdownViewer({ content, title }: MarkdownViewerProps) {
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(content);
      const button = document.activeElement as HTMLButtonElement;
      if (button) {
        const original = button.textContent;
        button.textContent = '✓ copied';
        setTimeout(() => button.textContent = original, 1000);
      }
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Simple markdown parsing for common elements
  const parseMarkdown = (text: string) => {
    return text
      // Headers
      .replace(/^### (.*$)/gm, '<h3 class="md-h3">$1</h3>')
      .replace(/^## (.*$)/gm, '<h2 class="md-h2">$1</h2>')
      .replace(/^# (.*$)/gm, '<h1 class="md-h1">$1</h1>')
      // Bold
      .replace(/\*\*(.*?)\*\*/g, '<strong class="md-bold">$1</strong>')
      // Italic
      .replace(/\*(.*?)\*/g, '<em class="md-italic">$1</em>')
      // Code blocks
      .replace(/```([\s\S]*?)```/g, '<pre class="md-code-block"><code>$1</code></pre>')
      // Inline code
      .replace(/`(.*?)`/g, '<code class="md-code">$1</code>')
      // Lists
      .replace(/^- (.*$)/gm, '<li class="md-list-item">$1</li>')
      // Line breaks
      .replace(/\n/g, '<br>');
  };

  return (
    <div className="markdown-viewer">
      <div className="markdown-header">
        {title && <h3 className="markdown-title">{title}</h3>}
        <button className="markdown-copy-btn" onClick={copyToClipboard}>
          📋 copy markdown
        </button>
      </div>
      <div 
        className="markdown-content"
        dangerouslySetInnerHTML={{ __html: parseMarkdown(content) }}
      />
    </div>
  );
}
