import react,{useState} from "react";

function MultipleFileUpload(){
    const [selectedFiles, setSelectedFiles]= useState([]);

    const handleFileChange= (event) =>{
        setSelectedFiles(event.target.files); //file lists
    };

    const handleSubmit= async (event)=> {
        event.preventDefault();
        if (selectedFiles.length > 0) {
            //handle file upload
            const formData = new FormData();
            formData.append("file",selectedFiles[0]); //method for only 1 file
            
            try{
                const response = await fetch("http://localhost:8000/api/upload",{
                    method:"POST",
                    body: formData,
                });
                if (response.ok){
                    const result= await response.json();
                    console.log("File processed:", result);

                }
                else{
                    console.error("Error uploading file");
                }
                

            }
            catch (error){
                console.error("Error:", error);
                
            }
            Array.from(selectedFiles).forEach(file => {
                console.log('Selected file:',file);
            });

        }
        else {
            console.log('no selected')
        }


    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input type="file" onChange ={handleFileChange}/>
                <button type="submit"> upload</button>  

            </form>

            {selectedFiles.length>0  && (
                <div>
                    <h4> File details:</h4>
                    <ul>
                        {Array.from(selectedFiles).map((file,index)=>(
                            <li key={index}>
                                Name:{file.name}, Type: {file.type}, Size: {file.size} bytes
                            </li>
                        ))}
                    </ul>

                </div>
            )}
        </div>
    );

}

export default MultipleFileUpload