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
  if block.t ~= "Header" or block.level ~= 3 then
    return false
  end
  local text = pandoc.utils.stringify(block.content)
  return text:match("^Cap[ií]tulo")
end

function Pandoc(doc)
  local blocks = {}
  for idx, block in ipairs(doc.blocks) do
    -- remove apenas a primeira quebra em branco no início do documento
    if idx == 1 and is_pagebreak(block) then
      goto continue
    end

    if is_chapter_heading(block) and not last_is_pagebreak(blocks) then
      table.insert(blocks, pandoc.RawBlock("latex", "\\clearpage"))
    end

    table.insert(blocks, block)
    ::continue::
  end

  return pandoc.Pandoc(blocks, doc.meta)
end
