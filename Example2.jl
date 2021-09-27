using Dash
using DashHtmlComponents
using DashVtk
using PyCall
using VTKDataIO
using VTKDataTypes

_image = read_vtk("head.vti");
dash_vtk = pyimport("dash_vtk");
pydata = PyVTK(_image);
dash_vtk_utils = pyimport("dash_vtk.utils");
dash_vtk_utils.to_volume_state;
volume_state = dash_vtk_utils.to_volume_state(pydata)

content = vtk_view(
        vtk_volumerepresentation(
        children = [
            vtk_volumecontroller(), 
            vtk_volume(state=volume_state),
        ]
    )
)

app = dash()

app.layout = html_div() do 
    html_div(
    style = Dict(
        "height" => "calc(100vh - 16px)",
        "width" => "100%" 
    ),
    children=[html_div(
        children=content,
        style = Dict(
            "height" => "100%",
            "width" => "100%"
        ),
    )],
    )
end

run_server(app, "0.0.0.0", debug = true)