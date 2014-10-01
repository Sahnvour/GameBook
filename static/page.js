window.onload = function () {

    var unescapeCode = function (safeText) {
        return safeText
            .replace(/\&amp\;/, '&')
            .replace(/\&lt\;/, '<')
            .replace(/\&gt\;/, '>')
            .replace(/\&quot\;/, '"')
            .replace(/\&#39\;/, '\'');
    };

    var renderer = new marked.Renderer();
    renderer.table = function (header, body) {
        return '<br/><table class="table">' + header + body + '</table>';
    };
    renderer.codespan = function (code) {
        return '<code>' + unescapeCode(code) + '</code>';
    };

    marked.setOptions({
        renderer: renderer,
        gfm: true,
        tables: true,
        breaks: false,
        pedantic: false,
        sanitize: true,
        smartLists: true,
        smartypants: false
    });

    var content = document.getElementById('content');
    var tokens = marked.lexer(content.innerHTML);

    tokens.forEach(function (token) {
        if (token.type === "code" || token.type === "codespan") {
            token.escaped = true;
        }
    });

    content.innerHTML = marked.parser(tokens);
};