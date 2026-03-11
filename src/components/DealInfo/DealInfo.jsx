import './DealInfo.sass'


export default function DealInfo({dealInfo,loading}) {
  return (
    <div className='editor-container'>
      {loading ? <div className="loading">Loading</div> : null}
      <img src={dealInfo.path} alt=""/>
    </div>
  )
}
