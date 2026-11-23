  function renderInline(esc) {
    // Fenced code has already been extracted before this runs; process
    // inline replacements on the escaped string.
    return esc
      // inline code
      .replace(/`([^`\n]+)`/g, (_m, c) => `<code>${c}</code>`)
      // bold
      .replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
      // italic
      .replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>")
      // safe links — only http(s) and mailto
      .replace(
        /\[([^\]\n]+)\]\((https?:\/\/[^\s)]+|mailto:[^\s)]+)\)/g,
        (_m, text, href) =>
          `<a href="${href}" target="_blank" rel="noopener noreferrer">${text}</a>`,
      );
  }
