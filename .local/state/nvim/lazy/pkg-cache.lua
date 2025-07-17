return {version=12,pkgs={{source="lazy",dir="/home/heyfang/.local/share/nvim/lazy/noice.nvim",name="noice.nvim",file="lazy.lua",spec=function()
return {
  -- nui.nvim can be lazy loaded
  { "MunifTanjim/nui.nvim", lazy = true },
  {
    "folke/noice.nvim",
  },
}

end,},{source="lazy",dir="/home/heyfang/.local/share/nvim/lazy/plenary.nvim",name="plenary.nvim",file="community",spec={"nvim-lua/plenary.nvim",lazy=true,},},{source="rockspec",dir="/home/heyfang/.local/share/nvim/lazy/telescope.nvim",name="telescope.nvim",file="telescope.nvim-scm-1.rockspec",spec={"telescope.nvim",specs={{"nvim-lua/plenary.nvim",lazy=true,},},build=false,},},},}