  function renderInline(esc) {
    // Fenced code has already been extracted before this runs; process
    // inline replacements on the escaped string.
    const links = [];
    let s = esc
      // inline code
      .replace(/`([^`\n]+)`/g, (_m, c) => `<code>${c}</code>`)
      // bold
      .replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
      // italic
      .replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>")
      // safe markdown links — only http(s) and mailto. Stash as a
      // placeholder so the bare-URL autolinker below can't re-wrap the
      // href we just emitted.
      .replace(
        /\[([^\]\n]+)\]\((https?:\/\/[^\s)]+|mailto:[^\s)]+)\)/g,
        (_m, text, href) => {
          links.push(
            `<a href="${href}" target="_blank" rel="noopener noreferrer">${text}</a>`,
          );
          return `\u0000LINK${links.length - 1}\u0000`;
        },
      )
      // autolink bare http(s) URLs (e.g. "Source: https://github.com/...").
      // Trailing sentence punctuation is kept outside the anchor.
      .replace(/(https?:\/\/[^\s<]+)/g, (m) => {
        const trail = /[.,;:!?)\]]+$/.exec(m);
        const url = trail ? m.slice(0, m.length - trail[0].length) : m;
        const tail = trail ? trail[0] : "";
        return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>${tail}`;
      });
    // Restore the stashed markdown links.
    return s.replace(/\u0000LINK(\d+)\u0000/g, (_m, i) => links[Number(i)]);
  }
