return {pkgs={{source="lazy",name="noice.nvim",file="lazy.lua",dir="/home/heyfang/.local/share/nvim/lazy/noice.nvim",spec=function()
return {
  -- nui.nvim can be lazy loaded
  { "MunifTanjim/nui.nvim", lazy = true },
  {
    "folke/noice.nvim",
  },
}

end,},{source="lazy",name="plenary.nvim",file="community",dir="/home/heyfang/.local/share/nvim/lazy/plenary.nvim",spec={"nvim-lua/plenary.nvim",lazy=true,},},},version=12,}