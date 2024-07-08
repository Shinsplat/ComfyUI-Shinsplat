import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { ComfyWidgets } from "../../scripts/widgets.js";
// ----------------------------------------------------------------------
//
// ----------------------------------------------------------------------
ComfyWidgets["SHINSPLAT_PI_MODULE"] = function(node, inputName, inputData, app) {

		async function loadFile(file) {

			// point to the target widget for the filename.
			const templateWidget = node.widgets.find((w) => w.name === "template");
			templateWidget.value = file.name

			var jShin = "";
			let shinRead = new FileReader();
			shinRead.readAsText(file, "utf-8");

			// callback
			shinRead.onloadend = function(){
				let shin_text = shinRead.result;
				// not needed ?
				let shin_template = shin_text.replace(/(\r\n|\n|\r)/gm,"");
				jShin = JSON.parse(shin_template);

				for (var prop in node.widgets)
				{
					if ( Object.prototype.hasOwnProperty.call(node.widgets, prop) )
					{
						var wName = node.widgets[prop].name;
						var wValue = node.widgets[prop].value;
						if( jShin.hasOwnProperty(wName) )
						{
							node.widgets[prop].value = jShin[wName];
						}
					}
				}
				// update the UI without having context first
				app.graph.setDirtyCanvas(true, false);
			}
		}
		// --------------------------------------------------------------
		//
		// --------------------------------------------------------------
		const fileInput = document.createElement("input");
		Object.assign(fileInput, {
			type: "file",
			accept: ".py, .txt, .json",
			style: "display: none",
			onchange: async () => {
				if (fileInput.files.length) {
					await loadFile(fileInput.files[0]);
				}
			},
		});
		document.body.append(fileInput);

		// button to select a file to import
		let loadWidget = node.addWidget("button", inputName, "MakeItYooNeek1", () => {
			fileInput.click();
		});

		loadWidget.label = "Load Template";
		loadWidget.serialize = false;

		// --------------------------------------------------------------
		// download / save
		// --------------------------------------------------------------
		//
		// --------------------------------------------------------------
		// paired with ...
		//		new JSave(jShout).download();
		// --------------------------------------------------------------
		var templateName = "data.json";
		class JSave {
			constructor(data={}) {
				this.data = data;
			}
			//download (type_of = "text/plain", filename= "data.txt") {
			download (type_of = "application/json", filename = templateName) {
				let body = document.body;
				const a = document.createElement("a");
				a.href = URL.createObjectURL(new Blob([JSON.stringify(this.data, null, 2)], {
					type: type_of
				}));
				a.setAttribute("download", filename);
				body.appendChild(a);
				a.click();
				body.removeChild(a);
			}
		} 
		// --------------------------------------------------------------
		// meat
		// --------------------------------------------------------------
		const fileOutput = document.createElement("output");
		document.body.append(fileOutput);
		// button to save parameters
		let saveWidget = node.addWidget("button", inputName, "MakeItYooNeek2", () => {
			var jShout = {};
			for (var prop in node.widgets)
			{
				if ( Object.prototype.hasOwnProperty.call(node.widgets, prop) )
				{
					var wName = node.widgets[prop].name;
					var wValue = node.widgets[prop].value;
					// While I don't need to do this I want to remind myself and keep the json clean
					if(wName === "upload") { continue; } // skip the property "MakeItYooNeek?"
					if(wName === "template") // I'm using this as the filename if it exists and is not "" or "empty".
					{
						if(wValue === "empty") { continue; } // default value?  I'm using data.json for that
						if(wValue.trim() === "") { continue; } // nothing but whitespace?
						templateName = wValue;
						continue;
					}
					if(wName === "name") // The preferred name will be this field
					{
						if(wValue === "empty") { continue; }
						if(wValue.trim() === "") { continue; }
						if(wValue.toLowerCase().endsWith(".json")) {
							templateName = wValue;
						} else {
							templateName = wValue + ".json";
						}
					}
					jShout[wName] = wValue;
				}
			}
			new JSave(jShout).download();
			// I think my block logic is goofed above, templateName retains its last
			// setting if it's blank in the UI *shrugs*.  Moving on, too much to do.
			templateName = "data.json";
		});
		saveWidget.label = "Save Template";
		saveWidget.serialize = false;
		// --------------------------------------------------------------
		// /ds
		// --------------------------------------------------------------
		return { widget: loadWidget };
};
app.registerExtension({
	name: "ShinsplatPIModule",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "Tensor Toys (Shinsplat)") {
			nodeData.input.required.upload = ["SHINSPLAT_PI_MODULE"];
		}
	}
});
