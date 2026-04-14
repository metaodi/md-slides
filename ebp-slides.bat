@echo off

set "arg1=%~1"
set "arg2=%~2"

if "%arg2%"=="" set "arg2=ebp_slides_output.pptx"


md-slides %arg1% --template templates\ebp_template.pptx -o %arg2%