import DaVinciResolveScript as dvr_script

resolve = dvr_script.scriptapp("Resolve")
projectManager = resolve.GetProjectManager()
projectManager.CreateProject("Donuts")
