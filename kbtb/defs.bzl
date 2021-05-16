def _kbpb_from_kle(ctx):
    output_file = ctx.actions.declare_file("{}.pb".format(ctx.label.name))
    ctx.actions.run(
        inputs = [ctx.file.src],
        outputs = [output_file],
        arguments = [
            "--input={}".format(ctx.file.src.path),
            "--output={}".format(output_file.path),
        ],
        executable = ctx.executable._from_kle,
    )
    return DefaultInfo(
        files = depset([output_file]),
        runfiles = ctx.runfiles([output_file]),
    )

kbpb_from_kle = rule(
    implementation = _kbpb_from_kle,
    attrs = {
        "src": attr.label(
            allow_single_file = [".json"],
            mandatory = True,
        ),
        "_from_kle": attr.label(
            default = Label("//kbtb/cli:from_kle"),
            executable = True,
            cfg = "exec",
        ),
    },
)

def _keyboard_plate_dxf(ctx):
    output_file = ctx.actions.declare_file("{}.dxf".format(ctx.label.name))
    ctx.actions.run(
        inputs = [ctx.file.src],
        outputs = [output_file],
        arguments = [
            "--input={}".format(ctx.file.src.path),
            "--output={}".format(output_file.path),
            "--plate_type={}".format(ctx.attr.plate_type),
            "--format=plate_dxf",
        ],
        executable = ctx.executable._toolbox,
    )
    return DefaultInfo(files = depset([output_file]))

keyboard_plate_dxf = rule(
    implementation = _keyboard_plate_dxf,
    attrs = {
        "src": attr.label(
            allow_single_file = [".pb"],
            mandatory = True,
        ),
        "plate_type": attr.string(
            default = "top",
        ),
        "_toolbox": attr.label(
            default = Label("//kbtb/cli:to_dxf"),
            executable = True,
            cfg = "exec",
        ),
    },
)

def _bomcpl_from_kicad(ctx):
    output_file = ctx.actions.declare_file("{}.zip".format(ctx.label.name))
    ctx.actions.run(
        inputs = [ctx.file.src],
        outputs = [output_file],
        arguments = [
            "--input={}".format(ctx.file.src.path),
            "--output={}".format(output_file.path),
        ],
        env = {"LD_LIBRARY_PATH": ctx.executable._bomcpl_from_kicad.path + ".runfiles/com_gitlab_kicad_kicad"},
        executable = ctx.executable._bomcpl_from_kicad,
    )
    return DefaultInfo(files = depset([output_file]))

bomcpl_from_kicad = rule(
    implementation = _bomcpl_from_kicad,
    attrs = {
        "src": attr.label(
            allow_single_file = [".kicad_pcb"],
            mandatory = True,
        ),
        "_bomcpl_from_kicad": attr.label(
            default = Label("//kbtb/cli:bomcpl_from_kicad"),
            executable = True,
            cfg = "exec",
        ),
    },
)
