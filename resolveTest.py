import DaVinciResolveScript as dvr_script

resolve = dvr_script.scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
#projectManager.CreateProject("Donuts")
proj = projectManager.GetCurrentProject()
print proj.GetName()
print proj
print proj.GetCurrentTimeline()
#projectManager.GetFrameRate()