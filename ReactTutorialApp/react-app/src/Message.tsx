// # function based components are more popular now

//PascalCase for function name
function Message(){
    // JSX: JAVASCRIPT XML
    const name = 'John Doe';
    if (name)
        return <h1>Hello World, {name} </h1>;
    else
        return <h1>Hello World, Guest</h1>;

}

export default Message;