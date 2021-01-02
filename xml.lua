http = require("socket.http")

function parseargs(s)
  local arg = {}
  string.gsub(s, "([%-%w]+)=([\"'])(.-)%2", function (w, _, a)
    arg[w] = a
  end)
  return arg
end
    
function collect(s)
  local stack = {}
  local top = {}
  table.insert(stack, top)
  local ni,c,label,xarg, empty
  local i, j = 1, 1
  while true do
    ni,j,c,label,xarg, empty = string.find(s, "<(%/?)([%w:]+)(.-)(%/?)>", i)
    if not ni then break end
    local text = string.sub(s, i, ni-1)
    if not string.find(text, "^%s*$") then
      table.insert(top, text)
    end
    if empty == "/" then  -- empty element tag
      table.insert(top, {label=label, xarg=parseargs(xarg), empty=1})
    elseif c == "" then   -- start tag
      top = {label=label, xarg=parseargs(xarg)}
      table.insert(stack, top)   -- new level
    else  -- end tag
      local toclose = table.remove(stack)  -- remove top
      top = stack[#stack]
      if #stack < 1 then
        error("nothing to close with "..label)
      end
      if toclose.label ~= label then
        error("trying to close "..toclose.label.." with "..label)
      end
      table.insert(top, toclose)
    end
    i = j+1
  end
  local text = string.sub(s, i)
  if not string.find(text, "^%s*$") then
    table.insert(stack[#stack], text)
  end
  if #stack > 1 then
    error("unclosed "..stack[#stack].label)
  end
  return stack[1]
end

-- https://stackoverflow.com/questions/41942289/display-contents-of-tables-in-lua
function tprint (tbl, indent)
  if not indent then indent = 0 end
  -- local toprint = string.rep(" ", indent) .. "{\n"
  local toprint = " {\n"
  indent = indent + 2
  for k, v in pairs(tbl) do
    toprint = toprint .. string.rep(" ", indent)
    if (type(k) == "number") then
      toprint = toprint .. "[" .. k .. "] = "
    elseif (type(k) == "string") then
      toprint = toprint  .. k ..  "= "
    end
    if (type(v) == "number") then
      toprint = toprint .. v .. ",\n"
    elseif (type(v) == "string") then
      toprint = toprint .. "\"" .. v .. "\",\n"
    elseif (type(v) == "table") then
      toprint = toprint .. tprint(v, indent + 2) .. ",\n"
    else
      toprint = toprint .. "\"" .. tostring(v) .. "\",\n"
    end
  end
  toprint = toprint .. string.rep(" ", indent-2) .. "}"
  return toprint
end

-- file = io.open("weather.gov", "r")
-- t = file:read("*all")
-- file:close()
http.request("https://forecast.weather.gov/MapClick.php?lat=39.54&lon=-104.91&unit=0&lg=english&FcstType=dwml")
x = collect(t)
dwml = x[2]
-- print("dwml:", dwml["label"])

dwml_head = dwml[1]
-- print("head:", dwml_head["label"])

dwml_head_product = dwml_head[1]
-- print("product:", dwml_head_product["label"])
dwml_head_product_creation = dwml_head_product[1]
-- print("creation:", dwml_head_product_creation["label"])
dwml_head_product_category = dwml_head_product[2]
-- print("creation:", dwml_head_product_category["label"])

dwml_head_source = dwml_head[2]
-- print("source:", dwml_head_source["label"])
dwml_head_source_production = dwml_head_source[1]
-- print("production:", dwml_head_source_production["label"])
dwml_head_source_credit = dwml_head_source[2]
-- print("credit:", dwml_head_source_credit["label"])
dwml_head_source_more = dwml_head_source[3]
-- print("more:", dwml_head_source_more["label"])

dwml_data = dwml[2]
-- print("data:", dwml_data["label"])

dwml_data_location = dwml_data[1]
-- print("location:", dwml_data_location["label"])

-- dwml_data_location_location = dwml_data_location[1]
-- print("location:", dwml_data_location_location["label"])

dwml_data_location_description = dwml_data_location[2]
-- print("description:", dwml_data_location_description[1])

dwml_data_location_point = dwml_data_location[3]
-- print("latitude:", dwml_data_location_point["xarg"]["latitude"])
-- print("longitude:", dwml_data_location_point["xarg"]["longitude"])

dwml_data_location_city = dwml_data_location[4]
-- print("city:", dwml_data_location_city[1])
-- print("start:", dwml_data_location_city["xarg"]["state"])

dwml_data_location_height = dwml_data_location[5]
-- print("height:", dwml_data_location_height[1])
-- print("height:", dwml_data_location_height["xarg"]["datum"])

dwml_data_moreWeatherInformation = dwml_data[2]
-- print("moreWeatherInformation:", dwml_data_moreWeatherInformation[1])

dwml_data_time = dwml_data[3]
for i, v in ipairs(dwml_data_time) do
  if v["label"] == "start" then
    -- print(v["xarg"]["period-name"])
  end
end

dwml_data_parameters = dwml_data[6]
-- print("parameters:", dwml_data_parameters["label"])

dwml_data_parameters_temperature_max = dwml_data_parameters[1]
for i, v in ipairs(dwml_data_parameters_temperature_max) do
  if v["label"] == "value" then
    -- print(v[1])
  end
end

dwml_data_parameters_temperature_min = dwml_data_parameters[2]
for i, v in ipairs(dwml_data_parameters_temperature_min) do
  if v["label"] == "value" then
    -- print(v[1])
  end
end

dwml_data_parameters_precipatation = dwml_data_parameters[3]
-- print("probability:", dwml_data_parameters_precipatation["label"])

dwml_data_parameters_weather = dwml_data_parameters[4]
for i, v in ipairs(dwml_data_parameters_weather) do
  if v["label"] == "weather" then
    print(v["xarg"]["weather-summary"])
  end
end

dwml_data_parameters_conditions = dwml_data_parameters[5]
for i, v in ipairs(dwml_data_parameters_conditions) do
  if v["label"] == "icon" then
    for j, w in ipairs(v) do
      print(w)
    end
  end
end

dwml_data_parameters_forecast = dwml_data_parameters[6]
for i, v in ipairs(dwml_data_parameters_forecast) do
  if v["label"] == "text" then
    for j, w in ipairs(v) do
      print(w)
    end
  end
end
