package_name = blend_et

subdirectories = tools annotations volume latex
additional_files = __init__.py reload.py

pyfiles = $(foreach dir,$(subdirectories),$(wildcard $(dir)/*.py)) $(additional_files)

target = "${package_name}.zip"

$(target) : $(pyfiles)
	@echo Creating zip file: $@ from: $^
	@rm -f $@
	@mkdir -p ${package_name}
	@cp -r $(subdirectories) ${package_name}/
	@cp $(additional_files) ${package_name}/
	@zip -r $@ ${package_name}/
	@rm -rf ${package_name}
	@echo Zip file created: $@

clean :
	@rm -f $(target)
	@rm -rf ${package_name}


all : $(target)

.PHONY: all clean