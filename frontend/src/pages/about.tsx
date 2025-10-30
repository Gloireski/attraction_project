// import { loa}


export async function clientLoader() {
  // you can now fetch data here
  return {
    title: "About page",
  };
}

interface LoaderData {
  title: string;
}

export default function Component({ loaderData }: { loaderData: LoaderData }) {
  return <h1>{loaderData.title}</h1>;
}
