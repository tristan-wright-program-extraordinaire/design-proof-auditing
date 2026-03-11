import './Attachment.sass'

import { useState,useEffect } from 'react'

export default function Attachment() {
    const [img, setImg] = useState();

    const fetchImage = async () => {
        const res = await fetch("*****PROPRIETARY INFO *****");
        const imageBlob = await res.blob();
        const imageObjectURL = URL.createObjectURL(imageBlob);
        setImg(imageObjectURL);
    };

    useEffect(() => {
        fetchImage();
    }, []);

    return (
        <div className='attachment-container'>
            <img src={img} alt="attachment" />
        </div>
    )
}
