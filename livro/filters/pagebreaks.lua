-- Pandoc filter: garante quebra de página antes de cada capítulo e remove a primeira
-- quebra manual que antecede o corpo (para evitar página em branco após a capa).

local function is_pagebreak(block)
  if block.t ~= "RawBlock" then
    return false
  end
  local format = string.lower(block.format or "")
  return (format == "latex" or format == "tex")
    and (block.text:match("\\newpage") or block.text:match("\\clearpage"))
  end

  local function last_is_pagebreak(blocks)
    local last = blocks[#blocks]
    return last and is_pagebreak(last)
end

local function is_chapter_heading(block)
  if block.t ~= "Header" then
    return false
  end
  local text = pandoc.utils.stringify(block.content):lower()
  return text:match("^cap")
end

local function is_part_heading(block)
  if block.t ~= "Header" or block.level ~= 1 then
    return false
  end
  local text = pandoc.utils.stringify(block.content)
  return text:match("^PARTE")
end

local function is_intro_heading(block)
  if block.t ~= "Header" or block.level ~= 1 then
    return false
  end
  local text = pandoc.utils.stringify(block.content)
  return text:match("^Introdu")
end

function Pandoc(doc)
  local blocks = {}
  for idx, block in ipairs(doc.blocks) do
    -- remove apenas a primeira quebra em branco no início do documento
    if idx == 1 and is_pagebreak(block) then
      goto continue
    end

    local intro = is_intro_heading(block)
    local part = is_part_heading(block)
    local chapter = is_chapter_heading(block)

    if intro then
      table.insert(blocks, pandoc.RawBlock("latex", "\\clearpage\\pagenumbering{arabic}"))
      block.classes = block.classes or {}
      table.insert(block.classes, "unnumbered")
    end

    if part then
      if not last_is_pagebreak(blocks) then
        table.insert(blocks, pandoc.RawBlock("latex", "\\clearpage"))
      end
      table.insert(blocks, pandoc.RawBlock("latex", "\\thispagestyle{empty}"))
      table.insert(blocks, pandoc.RawBlock("latex", "\\vspace*{\\fill}"))
      block.content = {pandoc.SmallCaps(block.content)}
      block.classes = block.classes or {}
      table.insert(block.classes, "unnumbered")
      -- encerra a página da parte centrada verticalmente
      table.insert(blocks, block)
      table.insert(blocks, pandoc.RawBlock("latex", "\\vspace*{\\fill}\\clearpage"))
      goto continue
    end

    if chapter then
      if not last_is_pagebreak(blocks) then
        table.insert(blocks, pandoc.RawBlock("latex", "\\clearpage"))
      end
      local attr = block.attr or pandoc.Attr()
      block = pandoc.Header(1, block.content, attr) -- eleva capítulos para o nível principal
      block.classes = block.classes or {}
      table.insert(block.classes, "unnumbered") -- mantém sem numeração visível
    elseif block.t == "Header" and block.level == 1 and not intro then
      -- demais headings de nível 1 ficam sem numeração para não interferir no contador
      block.classes = block.classes or {}
      table.insert(block.classes, "unnumbered")
    end

    table.insert(blocks, block)
    ::continue::
  end

  return pandoc.Pandoc(blocks, doc.meta)
end
